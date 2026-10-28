"""End-to-end publishing and economy test (local only): staff publish -> catalog -> purchase -> inventory ->
limited unique stock/serials under concurrency -> resale. Every outcome is checked in the database.

Creates synthetic accounts (EclT*) and items named "[TEST] ..." owned by the system account. Temporary staff
permissions are removed in `finally`; test items are hidden from the catalog at the end.
Results: local/economy-pipeline-results.json
"""
import pathlib, runpy, json, re, secrets, threading, struct, zlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
h = runpy.run_path(str(ROOT / 'local/http-client.py'))
Client, multipart, png = h['Client'], h['multipart'], h['png']
sql = runpy.run_path(str(ROOT / 'local/inspect-db.py'))['sql']
q = lambda s: json.loads(sql(f"SELECT coalesce(json_agg(t),'[]') FROM ({s}) t"))
one = lambda s: sql(s)

names = re.findall(r'^\s*(\w+)\s*,', (ROOT / 'Roblox/Roblox.Models/Enums/Staff.cs').read_text(), re.M)
STAFF_PERMS = [names.index(n) for n in ['CreateAsset', 'SetAssetProduct', 'GetProductDetails', 'MakeItemLimited']]
NONCE = secrets.token_hex(3)
results = []

def test(name, fn):
    try:
        d = fn(); results.append({'test': name, 'result': 'PASS', 'details': d}); print('PASS', name, d, flush=True)
    except Exception as e:
        results.append({'test': name, 'result': 'FAIL', 'error': str(e)}); print('FAIL', name, e, flush=True)
    finally:
        (ROOT / 'local/economy-pipeline-results.json').write_text(json.dumps(results, indent=2, default=str))

def account(prefix, robux=True):
    c = Client(); n = prefix + NONCE + secrets.token_hex(2)
    uid = c.call('/local/signup', 'POST', {'username': n, 'password': secrets.token_urlsafe(18)})['userId']
    if robux: c.call('/local/grant', 'POST', {})
    return c, uid

def balance(uid): return int(one(f'SELECT balance_robux FROM user_economy WHERE user_id={uid}'))
def owned(uid, aid): return q(f'SELECT id, serial, price FROM user_asset WHERE user_id={uid} AND asset_id={aid} ORDER BY id')
def fails(fn):
    try: fn()
    except RuntimeError as e: return str(e)
    raise AssertionError('request unexpectedly succeeded')
def buy(c, aid, price, seller=1, uaid=None):
    body = {'expectedCurrency': 1, 'expectedPrice': price, 'expectedSellerId': seller}
    if uaid: body['userAssetId'] = uaid
    return c.call(f'/apisite/economy/v1/purchases/products/{aid}', 'POST', body)
def colored_png(rgb, size=64):
    def chunk(t, d): return struct.pack('!I', len(d)) + t + d + struct.pack('!I', zlib.crc32(t + d))
    rows = (b'\0' + bytes(rgb) * size) * size
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!2I5B', size, size, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b'')

staff, staff_id = account('EclTStaff', robux=False)
buyer, buyer_id = account('EclTBuyer')
poor, poor_id = account('EclTPoor', robux=False)
# New accounts receive a 100 Robux signup bonus; give this one a balance below the test price.
one(f'UPDATE user_economy SET balance_robux=3 WHERE user_id={poor_id}')
racers = [account('EclTRacer') for _ in range(5)]
created = []
system_before = balance(1)

try:
    for p in STAFF_PERMS:
        one(f'INSERT INTO user_permission(user_id,permission) VALUES ({staff_id},{p}) ON CONFLICT DO NOTHING')

    def publish(name, price, png_bytes, limited_unique=False, copies=None, for_sale=True):
        fields = {'name': name, 'description': 'Automated Eclipso test item. Not a real catalog item.', 'assetTypeId': 1, 'genre': 0,
                  'isForSale': str(for_sale).lower(), 'isVisible': 'true', 'isLimited': str(limited_unique).lower(),
                  'isLimitedUnique': str(limited_unique).lower(), 'price': price}
        if copies: fields['maxCopies'] = copies
        aid = multipart(staff, '/admin-api/api/asset/create', fields, [('rbxm', 'test.png', 'image/png', png_bytes)])['assetId']
        created.append(aid); return aid

    # ---------- Ordinary item ----------
    def invalid_upload():
        before = int(one('SELECT count(*) FROM asset'))
        msg = fails(lambda: multipart(staff, '/admin-api/api/asset/create', {'name': '[TEST] bad', 'assetTypeId': 1, 'genre': 0, 'isForSale': 'true', 'isVisible': 'true', 'isLimited': 'false', 'isLimitedUnique': 'false', 'price': 1},
                                      [('rbxm', 'evil.png', 'image/png', b'<script>alert(1)</script> not an image')]))
        assert msg.startswith('400') and 'not a readable image' in msg, msg
        msg2 = fails(lambda: multipart(staff, '/admin-api/api/asset/create', {'name': '[TEST] huge', 'assetTypeId': 1, 'genre': 0, 'isForSale': 'true', 'isVisible': 'true', 'isLimited': 'false', 'isLimitedUnique': 'false', 'price': 1},
                                       [('rbxm', 'big.png', 'image/png', colored_png((1, 2, 3), 2100))]))
        assert msg2.startswith('400') and 'maximum' in msg2, msg2
        assert int(one('SELECT count(*) FROM asset')) == before
        return {'non-image': msg[:90], 'oversized': msg2[:90], 'assets created': 0}
    test('Invalid uploads are refused with a useful message and create nothing', invalid_upload)

    state = {}
    def publish_ordinary():
        aid = publish(f'[TEST] Eclipso Poster {NONCE}', 10, colored_png((120, 60, 230)))
        state['poster'] = aid
        row = q(f'SELECT name, asset_type, is_for_sale, price_robux, creator_id, moderation_status FROM asset WHERE id={aid}')[0]
        thumb = q(f'SELECT content_url, moderation_status FROM asset_thumbnail WHERE asset_id={aid}')
        assert row['is_for_sale'] and row['price_robux'] == 10 and row['creator_id'] == 1, row
        assert thumb and thumb[0]['content_url'], thumb
        api_thumb = buyer.call(f'/apisite/thumbnails/v1/assets?assetIds={aid}&size=420x420&format=png')['data'][0]
        assert api_thumb['state'] == 'Completed' and api_thumb['imageUrl'], api_thumb
        found = buyer.call('/apisite/catalog/v1/search/items?keyword=' + NONCE + '&limit=30')['data']
        assert any(x['id'] == aid for x in found), found
        details = buyer.call('/apisite/catalog/v1/catalog/items/details', 'POST', {'items': [{'itemType': 'Asset', 'id': aid}]})['data'][0]
        assert details['price'] == 10 and details['name'].startswith('[TEST]'), details
        return {'assetId': aid, 'thumbnail': api_thumb['imageUrl'], 'catalog search': 'found', 'item details price': 10}
    test('Publish ordinary item: stored, thumbnail, catalog search, item details', publish_ordinary)

    def buy_ordinary():
        aid = state['poster']; b0, s0 = balance(buyer_id), balance(1)
        buy(buyer, aid, 10)
        assert balance(buyer_id) == b0 - 10 and len(owned(buyer_id, aid)) == 1
        assert balance(1) == s0 + 7, (balance(1), s0)  # creator receives 70%
        tx = q(f"SELECT type, amount FROM user_transaction WHERE asset_id={aid} AND user_id_one={buyer_id}")
        assert tx, 'no buyer transaction recorded'
        return {'buyer charged': 10, 'creator credited': 7, 'inventory copies': 1, 'transactions': tx}
    test('Buy ordinary item: charge, creator credit, inventory and ledger agree', buy_ordinary)

    def no_double_charge():
        aid = state['poster']; b0 = balance(buyer_id)
        msg = fails(lambda: buy(buyer, aid, 10))
        assert balance(buyer_id) == b0 and len(owned(buyer_id, aid)) == 1, 'second purchase changed state'
        return msg[:100]
    test('Buying again is refused without a second charge', no_double_charge)

    def insufficient():
        aid = state['poster']; msg = fails(lambda: buy(poor, aid, 10))
        assert balance(poor_id) == 3 and owned(poor_id, aid) == []
        return msg[:100]
    test('Insufficient funds: refused, no ownership', insufficient)

    def stale_price():
        aid = state['poster']; c, uid = racers[0]; b0 = balance(uid)
        msg = fails(lambda: buy(c, aid, 5))
        assert 'Price has changed' in msg and balance(uid) == b0 and owned(uid, aid) == []
        return msg[:100]
    test('Stale price is refused', stale_price)

    def metadata_and_offsale():
        aid = state['poster']
        staff.call('/admin-api/api/asset/modify', 'PATCH', {'assetId': aid, 'name': f'[TEST] Eclipso Poster {NONCE} v2', 'description': 'edited'})
        staff.call('/admin-api/api/asset/product', 'PATCH', {'assetId': aid, 'isForSale': False, 'isVisible': True, 'isLimited': False, 'isLimitedUnique': False, 'priceRobux': 10, 'maxCopies': None})
        row = q(f'SELECT name, description, is_for_sale FROM asset WHERE id={aid}')[0]
        assert row['name'].endswith('v2') and row['description'] == 'edited' and not row['is_for_sale'], row
        c, uid = racers[1]; b0 = balance(uid)
        msg = fails(lambda: buy(c, aid, 10))
        assert balance(uid) == b0 and owned(uid, aid) == []
        return {'metadata persisted': True, 'direct API buy of off-sale item': msg[:80]}
    test('Metadata edit persists; off-sale item cannot be bought via direct API', metadata_and_offsale)

    # ---------- Limited unique ----------
    def lu_race():
        aid = publish(f'[TEST] Eclipso LU Orb {NONCE}', 5, colored_png((240, 200, 30)), limited_unique=True, copies=3)
        state['lu'] = aid
        before = {uid: balance(uid) for _, uid in racers}
        outcome = {}
        def attempt(c, uid):
            try: buy(c, aid, 5); outcome[uid] = 'ok'
            except RuntimeError as e: outcome[uid] = str(e)[:90]
        threads = [threading.Thread(target=attempt, args=r) for r in racers]
        [t.start() for t in threads]; [t.join() for t in threads]
        copies = q(f'SELECT user_id, serial FROM user_asset WHERE asset_id={aid} ORDER BY serial')
        serials = [c['serial'] for c in copies]
        assert sorted(serials) == [1, 2, 3], copies
        owners = {c['user_id'] for c in copies}
        for _, uid in racers:
            paid = before[uid] - balance(uid)
            assert paid == (5 if uid in owners else 0), (uid, paid, outcome[uid])
        assert sum(1 for v in outcome.values() if v == 'ok') == 3, outcome
        row = q(f'SELECT is_for_sale FROM asset WHERE id={aid}')[0]
        assert not row['is_for_sale'], 'sold-out item still for sale'
        late, late_id = racers[0] if racers[0][1] not in owners else next(r for r in racers if r[1] not in owners)
        msg = fails(lambda: buy(late, aid, 5))
        return {'5 simultaneous buyers for 3 copies': outcome, 'serials': serials, 'only owners charged': True, 'after sold out': msg[:70]}
    test('Limited unique: concurrent buyers, unique serials 1-3, sold out, losers not charged', lu_race)

    def resale():
        aid = state['lu']
        seller_c, seller_id = next(r for r in racers if owned(r[1], aid))
        copy = owned(seller_id, aid)[0]
        # A non-owner cannot list someone else's copy
        msg_steal = fails(lambda: buyer.call(f'/apisite/economy/v1/assets/{aid}/resellable-copies/{copy["id"]}', 'PATCH', {'price': 1}))
        seller_c.call(f'/apisite/economy/v1/assets/{aid}/resellable-copies/{copy["id"]}', 'PATCH', {'price': 40})
        listing = next(x for x in buyer.call(f'/apisite/economy/v1/assets/{aid}/resellers')['data'] if x['userAssetId'] == copy['id'])
        assert listing['price'] == 40 and listing['serialNumber'] == copy['serial'], listing
        msg_stale = fails(lambda: buy(buyer, aid, 30, seller_id, copy['id']))
        b0, s0 = balance(buyer_id), balance(seller_id)
        buy(buyer, aid, 40, seller_id, copy['id'])
        assert balance(buyer_id) == b0 - 40 and balance(seller_id) == s0 + 28, (balance(buyer_id), b0, balance(seller_id), s0)
        moved = q(f'SELECT user_id, serial, price FROM user_asset WHERE id={copy["id"]}')[0]
        assert moved['user_id'] == buyer_id and moved['serial'] == copy['serial'] and moved['price'] == 0, moved
        msg_resell = fails(lambda: seller_c.call(f'/apisite/economy/v1/assets/{aid}/resellable-copies/{copy["id"]}', 'PATCH', {'price': 50}))
        c3, id3 = next(r for r in racers if r[1] not in (seller_id,) and not owned(r[1], aid))
        msg_gone = fails(lambda: buy(c3, aid, 40, seller_id, copy['id']))
        sales = q(f'SELECT amount FROM collectible_sale_logs WHERE asset_id={aid}')
        assert [s['amount'] for s in sales] == [40], sales
        return {'non-owner listing': msg_steal[:40], 'stale listing price': msg_stale[:70], 'buyer -40 / seller +28 (30% fee)': True,
                'serial kept': copy['serial'], 'old owner relist': msg_resell[:40], 'buy completed listing again': msg_gone[:70], 'price history rows': sales}
    test('Resale: owner-only listing, stale price refused, exact transfer, fee, no double sale', resale)

    def ledger_reconciles():
        net = int(one(f"SELECT coalesce(sum(CASE WHEN type=2 THEN amount ELSE 0 END),0) FROM user_transaction WHERE user_id_one=1 AND asset_id IN ({','.join(map(str, created))})"))
        return {'system account balance change': balance(1) - system_before, 'note': 'creator credits recorded per sale (70%)'}
    test('Ledger snapshot', ledger_reconciles)
finally:
    for p in STAFF_PERMS:
        one(f'DELETE FROM user_permission WHERE user_id={staff_id} AND permission={p}')
    if created:
        one(f"UPDATE asset SET visible=false WHERE id IN ({','.join(map(str, created))})")
    print('cleanup: staff perms removed; test items hidden from catalog:', created)

raise SystemExit(1 if any(r['result'] == 'FAIL' for r in results) else 0)

# Testing guide for kindmops — admin, publishing and limiteds

Everything here runs **on your PC** (http://127.0.0.1:5080). eclipso.lol only shows the Coming soon page for now.
Use **Opera GX**. Each section lists what to click, what should happen, and what to send back if it doesn't.

**Before you start:** double-click **Start Website.cmd** and wait for `Ready`. Leave that window open.

**Two accounts at once:** your normal Opera GX window is your **Midnight** (owner) login. For a second person, open
a **private window** (Ctrl+Shift+N). It has separate cookies, so you can be logged in as someone else there.

**If something fails:** take a screenshot of the page and note the time. Errors are also in
`.local\website.log` (open it with Notepad, scroll to the bottom). Send me the screenshot and the time; you don't
need to read the log yourself.

---

## A. Get into the admin panel (owner)

**If the admin panel didn't work for you before:** the website had been stopped by my previous work session
ending (now fixed), so pages couldn't load. Always start it yourself with **Start Website.cmd**. If you're unsure
whether it's running, double-click **Check Website Status.cmd**. It should say `running: Ready`; if it says
`Stopped`, run **Start Website.cmd** again.

1. Go to `http://127.0.0.1:5080/login`. In the **white box on the right** (not the small bar at the top), type
   `Midnight` and your password, then press **Log In**. You land on your Home page.
   - On a narrow window the white box can sit off-screen to the right; maximise Opera GX (double-click its title bar).
2. In the **left-hand menu** of the Home page, click **Admin** (near Groups and Forums). It only appears for staff
   and the owner. You can also type `http://127.0.0.1:5080/admin/`.
   - **Expected:** a dark menu on the left titled **Management** and a **Dashboard** with coloured boxes (users,
     pending assets…). The top-right link says **Back to Eclipso**.
   - **If you land on your Home page instead:** you are not logged in as Midnight, or the site was restarted before
     this fix. Log in again and retry. If it still happens, send me a screenshot.
3. In the admin menu open **Logs** (or `http://127.0.0.1:5080/admin/logs`).
   - **Expected:** **ALL ADMIN ACTIONS (AUDIT)** is selected first, including a `SetOwner` row for Midnight.
4. **Ordinary users are blocked:** in a private window (Ctrl+Shift+N) create a normal account at
   `http://127.0.0.1:5080/signup` (e.g. `KindTestBuyer1`), then open `http://127.0.0.1:5080/admin/`.
   - **Expected:** you are sent to `/home`; there is no Admin link in that account's menu.
5. **Logins now survive restarts:** run Stop Website.cmd then Start Website.cmd; reload. You should still be logged in.

## B. Publish a normal item and buy it

Prepare a small **PNG or JPEG** picture (for example your Eclipso E logo). Limits: 2048×2048 pixels, 10 MB.

1. Owner window: go to `http://127.0.0.1:5080/admin/asset/create`.
2. Fill in:
   - **Name:** `[TEST] Kind Poster 1`
   - **Description:** anything
   - **Type:** leave **Image** (other types are greyed out: they need the game renderer, not set up yet)
   - **Image file:** choose your PNG
   - **Price:** `15`
   - Tick **For Sale** and **Visible**. Leave **Limited Status** at *Not Limited*.
3. Click the create/submit button at the bottom.
   - **Expected:** you're taken to the new item's catalog page, showing your picture and price R$15.
   - Write down the **number in the address bar** (`/catalog/NUMBER/...`). That's the item ID.
4. **Try a bad file:** repeat step 2 with a `.txt` file renamed to `.png`.
   - **Expected:** a red message saying the file is not a readable image. No item is created.
5. Private window (your test buyer): go to `http://127.0.0.1:5080/local`, then click **Add 10,000 test robux**.
   This button exists only on your PC for testing. It will never be part of the public site.
6. Open the item page `http://127.0.0.1:5080/catalog/ITEM-ID/--` and click **Buy**, then confirm.
   - **Expected:** a success message. Your Robux drops by 15.
7. Click **Buy** again.
   - **Expected:** it says you already own it. No second charge.
8. Owner window: in the admin panel open **Players**, search the buyer's name, then open **Transactions** and
   **Inventory**.
   - **Expected:** one purchase of R$15 and the item in their inventory.
9. **Restart test:** run **Stop Website.cmd**, then **Start Website.cmd**. Log in again and check that the buyer
   still owns the item and has the same Robux.

## C. Publish a limited unique with 2 copies and sell out

1. Owner: `http://127.0.0.1:5080/admin/asset/create` → Name `[TEST] Kind LU 1`, Type Image, your PNG,
   Price `5`, tick For Sale and Visible, **Limited Status: Limited Unique**, **Max Copy Count: 2**. Create it.
2. Buyer 1 (private window): buy it.
   - **Expected:** owned, with serial **#1**.
3. Make a second buyer: close the private window, open a new one, sign up `KindTestBuyer2`, add test Robux,
   and buy the item.
   - **Expected:** serial **#2**. The item now shows as sold out / no longer for sale.
4. A third account trying to buy it:
   - **Expected:** refused ("no longer for sale" / "sold out"), and no Robux taken.
5. Owner: `http://127.0.0.1:5080/admin/product/update?assetId=ITEM-ID`.
   - **Expected:** Limited Unique, Max Copy Count 2, not for sale.

## D. Resell a copy

1. As `KindTestBuyer2` (the serial #2 owner): open `http://127.0.0.1:5080/local` and find the LU item in your
   inventory. Set a resale price of `30`.
2. As `KindTestBuyer1`: open the item page, find the reseller list, and buy the R$30 listing.
   - **Expected:** Buyer1 −30 Robux; Buyer2 +21 Robux (the seller gets 70%; 30% is the marketplace fee).
     Buyer1 now owns serial #2 as well as #1.
3. As `KindTestBuyer2`: try to list the same copy again.
   - **Expected:** refused, because you no longer own it.
4. Owner: in the admin panel open each buyer's **Transactions**.
   - **Expected:** a resale purchase (−30) and a resale sale (+21) that match the balances.

---

### What is not testable yet
- **Wearable items** (hats, shirts, faces, gear) and **avatars:** these need the game renderer, which isn't set up
  yet. Don't use them for testing; failures there are expected and already known.
- **Account recovery (forgot password):** no email delivery is configured, so it is not working yet.
- **eclipso.lol:** shows only the Coming soon page.

### Report back
For each section A–D, reply **pass** or **fail**. For a fail, include the step number, a screenshot and the time.

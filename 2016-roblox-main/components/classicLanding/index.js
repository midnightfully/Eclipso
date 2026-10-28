import { useEffect, useState } from 'react';
import Head from 'next/head';
import AuthenticationStore from '../../stores/authentication';
import styles from './landing.module.css';

const months = ['January','February','March','April','May','June','July','August','September','October','November','December'];
async function accountRequest(path, body) {
  let token = '';
  for (let attempt = 0; attempt < 2; attempt++) {
    const response = await fetch(path, { method: 'POST', credentials: 'same-origin',
      headers: {'Content-Type':'application/json', 'x-csrf-token':token}, body:JSON.stringify(body) });
    if (response.status === 403 && response.headers.get('x-csrf-token') && attempt === 0) {
      token = response.headers.get('x-csrf-token'); continue;
    }
    const text = await response.text(); let data = {};
    try { data = text ? JSON.parse(text) : {}; } catch { throw Error('The server could not complete this request. Please try again.'); }
    if (!response.ok) throw Error(data.errors?.[0]?.message || data.title || 'Unable to complete this request.');
    return data;
  }
  throw Error('Please enable cookies and try again.');
}
export default function ClassicLanding({ loginOnly = false }) {
  const auth = AuthenticationStore.useContainer();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [year, setYear] = useState(''); const [month, setMonth] = useState(''); const [day, setDay] = useState('');
  const [gender, setGender] = useState('Unknown');
  const currentYear = new Date().getFullYear();
  const days = month && year ? new Date(Number(year), Number(month), 0).getDate() : 31;
  useEffect(() => { if (auth.isAuthenticated) window.location.replace('/home'); }, [auth.isAuthenticated]);
  useEffect(() => { if (Number(day) > days) setDay(''); }, [days, day]);
  async function submit(event, signup) {
    event.preventDefault(); if (busy) return;
    const form = new FormData(event.currentTarget); setError('');
    if (signup && form.get('password') !== form.get('confirm')) { setError('Your passwords do not match.'); return; }
    setBusy(true);
    try {
      if (signup) await accountRequest('/apisite/auth/v2/signup', {
        username:form.get('username').trim(), password:form.get('password'),
        birthday:year+'-'+month.padStart(2,'0')+'-'+day.padStart(2,'0'), gender, acceptTerms:form.get('terms') === 'on'
      });
      else await accountRequest('/apisite/auth/v2/login', {ctype:'username',cvalue:form.get('username').trim(),password:form.get('password')});
      window.location.assign('/home');
    } catch (e) { setError(e.message); setBusy(false); }
  }
  return <div className={styles.page}>
    <Head><title>{loginOnly ? 'Log In' : 'Sign Up'} · 2017 Revival</title><meta name="description" content="An independent revival of the 2017 Roblox website." /></Head>
    <header className={styles.topbar}><div className={styles.topinner}>
      <nav aria-label="Main navigation"><a className={styles.mark} href="/" aria-label="Home"/><a href="#play">Play</a><a href="#about">About</a><a href="#platforms">Platforms</a></nav>
      <form className={styles.quickLogin} onSubmit={e=>submit(e,false)} aria-label="Quick login">
        <input name="username" placeholder="Username" aria-label="Login username" autoComplete="username" required disabled={busy}/>
        <input name="password" type="password" placeholder="Password" aria-label="Login password" autoComplete="current-password" required disabled={busy}/>
        <button disabled={busy}>Log In</button>
      </form>
    </div></header>
    <main id="play" className={styles.hero}><div className={styles.heroInner}>
      <div className={styles.brand}><img src="/img/roblox_logo.svg" alt="ROBLOX"/><p>Powering Imagination<sup>™</sup></p><span className={styles.revival}>an independent 2017 revival</span></div>
      <section className={styles.panel} aria-labelledby="signup-title">
        <h1 id="signup-title">{loginOnly ? 'LOG IN AND START HAVING FUN!' : 'SIGN UP AND START HAVING FUN!'}</h1>
        <form onSubmit={e=>submit(e,!loginOnly)}>
          {!loginOnly && <fieldset className={styles.birthday}><legend className={styles.srOnly}>Birthday</legend><span>Birthday</span>
            <select aria-label="Birth month" value={month} onChange={e=>setMonth(e.target.value)} required disabled={busy}><option value="">Month</option>{months.map((m,i)=><option value={String(i+1)} key={m}>{m}</option>)}</select>
            <select aria-label="Birth day" value={day} onChange={e=>setDay(e.target.value)} required disabled={busy}><option value="">Day</option>{Array.from({length:days},(_,i)=><option key={i} value={String(i+1)}>{i+1}</option>)}</select>
            <select aria-label="Birth year" value={year} onChange={e=>setYear(e.target.value)} required disabled={busy}><option value="">Year</option>{Array.from({length:currentYear-1899},(_,i)=><option key={i} value={String(currentYear-i)}>{currentYear-i}</option>)}</select>
          </fieldset>}
          <label className={styles.srOnly} htmlFor="account-name">Username</label><input id="account-name" name="username" placeholder={loginOnly ? 'Username' : "Username (don't use your real name)"} autoComplete="username" minLength={3} maxLength={20} required disabled={busy}/>
          <label className={styles.srOnly} htmlFor="account-password">Password</label><input id="account-password" name="password" type="password" placeholder="Password (minimum length 8)" autoComplete={loginOnly ? 'current-password' : 'new-password'} minLength={8} maxLength={128} required disabled={busy}/>
          {!loginOnly && <><label className={styles.srOnly} htmlFor="account-confirm">Confirm password</label><input id="account-confirm" name="confirm" type="password" placeholder="Confirm Password" autoComplete="new-password" minLength={8} required disabled={busy}/>
          <fieldset className={styles.gender}><legend className={styles.srOnly}>Gender (optional)</legend><span>Gender</span>{[['Female','♀'],['Male','♂']].map(([value,icon])=><button key={value} type="button" aria-label={value} aria-pressed={gender===value} onClick={()=>setGender(gender===value?'Unknown':value)} disabled={busy}>{icon}</button>)}</fieldset>
          <label className={styles.terms}><input type="checkbox" name="terms" required disabled={busy}/><span>By clicking Sign Up, you agree to the <a href="/info/revival#terms">revival terms</a> and <a href="/info/revival#privacy">privacy information</a>.</span></label></>}
          {error && <p className={styles.error} role="alert">{error}</p>}
          <button className={styles.submit} disabled={busy}>{busy ? 'Please wait…' : loginOnly ? 'Log In' : 'Sign Up'}</button>
          <p className={styles.alternate}>{loginOnly ? <>New here? <a href="/">Create an account</a></> : <>Already have an account? <a href="/login">Log in</a></>}</p>
        </form>
      </section>
    </div><p className={styles.credit}>Game: ROBLOX Point · Developer: StarMarine614</p></main>
    <section id="about" className={styles.about}><h2>Build friendships. Rediscover 2017.</h2><p>Create your revival account, meet friends, start a group and explore the catalog.</p><p>This is an independent community project, not the official Roblox service. Accounts and currency belong to this revival.</p></section>
    <section id="platforms" className={styles.platforms}><h2>Start in your browser</h2><p>The website is available for desktop browsers. Game clients and multiplayer are still in development.</p><a href="/catalog">Explore the catalog</a></section>
    <footer className={styles.footer}><a href="/info/revival">About this revival</a><a href="/info/revival#privacy">Privacy</a><a href="/info/revival#terms">Terms</a><span>2017 Revival</span></footer>
  </div>;
}

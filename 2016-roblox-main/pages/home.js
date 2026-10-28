import React, { useEffect } from 'react';
import AuthenticationStore from '../stores/authentication';
import MyDashboard from '../components/myDashboard';
import DashboardStore from '../components/myDashboard/stores/dashboardStore';
import Theme2016 from '../components/theme2016';

export default function AuthenticatedHomePage() {
  const auth = AuthenticationStore.useContainer();
  // Logged-out visitors get the signup page instead of an empty dashboard.
  useEffect(() => {
    if (!auth.isPending && !auth.isAuthenticated) window.location.replace('/');
  }, [auth.isPending, auth.isAuthenticated]);
  if (!auth.isAuthenticated) return null;
  return <Theme2016>
    <DashboardStore.Provider>
      <MyDashboard></MyDashboard>
    </DashboardStore.Provider>
  </Theme2016>
}

export const getStaticProps = () => {
  return {
    props: {
      title: 'Home - Eclipso',
    },
  }
}
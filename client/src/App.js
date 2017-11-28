import React from 'react';
import { Route } from 'react-router-dom';
import PropTypes from 'prop-types';

import SignupForm from './containers/signup_form';
import LoginPage from './components/pages/login_page';
import NavbarComponent from './components/navbar_component';
import DashboardPage from './components/pages/dashboard_page';
import UserRoute from './components/routes/user_routes';
import GuestRoute from './components/routes/guest_routes';

const App = ({ location }) => (
    <div>
        <NavbarComponent />
        <div className = "container">
            <Route path="/" exact component={LoginPage} />
            <GuestRoute location={location} path="/signup" exact component={SignupForm} />
            <GuestRoute location={location} path="/login" exact component={LoginPage} />
            <UserRoute location={location} path="/myQLoop" exact component={DashboardPage} />
        </div>
    </div>
);

App.propTypes = {
    location: PropTypes.shape({
        pathname: PropTypes.string.isRequired
    }).isRequired
};

export default App;

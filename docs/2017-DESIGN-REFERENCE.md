# 2017 signup reference and implementation

Baseline: the screenshot supplied by kindmops in this conversation, showing the red 2017 Roblox wordmark, Powering Imagination, blue sky/red coaster, a compact teal navigation strip, top-right login fields, a white signup panel, birthday selectors, username/password/confirmation, gender choices and a green signup action.

The local landing page implements this layout. It identifies the independent revival and uses its own account service. The login page shares the same presentation. Authentication, validation and results come from the local backend; no real Roblox account flow is used.

Artwork: public/img/revival/coaster.jpg was downloaded from https://images.mein-mmo.de/magazin/medien/2017/03/roblox-achterbahn.jpg (970 × 626), associated with the 2017 article https://mein-mmo.de/roblox-48-mio/. The asset is a historical visual reference; upstream/source attribution does not establish redistribution rights for every image. Preserve attribution and resolve the public asset set before launch.

Code:
- components/classicLanding/index.js and landing.module.css
- pages/index.js, login.js, signup.js
- pages/info/revival.js
- Controllers/v2/Authentication.cs and WebsiteModels/Response/Authentication/Signup.cs

This is the first 2017 page conversion. Home, catalog, profile, groups, inventory, avatar, create, trade, settings and Builders Club still need individual historical comparison and browser testing. The existing frontend folder name is not a version guarantee.

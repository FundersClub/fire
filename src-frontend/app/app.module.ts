import { ApplicationRef, NgModule } from '@angular/core';
import { MaterialModule } from '@angular/material';
import { BrowserModule }  from '@angular/platform-browser';
import { RouterModule }   from '@angular/router';

import { AppComponent } from './app.component';
import { ManageAddressComponent } from './manage-address.component';
import { ManageSettingsComponent } from './manage-settings.component';
import { ManageTeamComponent } from './manage-team.component';

@NgModule({
    imports: [
        BrowserModule,
        MaterialModule,
        RouterModule.forRoot([{
            path: '',
            component: ManageAddressComponent,
        }, {
            path: 'team',
            component: ManageTeamComponent,
        }, {
            path: 'settings',
            component: ManageSettingsComponent,
        }]),
    ],
    declarations: [
        AppComponent,
        ManageAddressComponent,
        ManageSettingsComponent,
        ManageTeamComponent,
    ],
    entryComponents: [
        AppComponent,
    ],
})
export class AppModule {
    ngDoBootstrap(appRef: ApplicationRef) {
        // In some cases we don't actually want to kick off anything (e.g.
        // we're loading a purely static page). If that global flag is set,
        // quit here.
        if (window['preventBootstrap']) {
            return;
        }

        appRef.bootstrap(AppComponent);
    }
}

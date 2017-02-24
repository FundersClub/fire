import { ApplicationRef, NgModule } from '@angular/core';
import { MaterialModule } from '@angular/material';
import { BrowserModule }  from '@angular/platform-browser';
import { RouterModule, Routes }   from '@angular/router';
import { HttpModule }    from '@angular/http';

import { AppComponent } from './app.component';
import { ManageAddressComponent } from './manage-address.component';
import { ManageSettingsComponent } from './manage-settings.component';
import { ManageTeamComponent } from './manage-team.component';
import { RepositoryComponent } from './repository.component';
import { RepositoryListComponent } from './repository-list.component';
import { UserService } from './user.service';

const appRoutes: Routes = [{
    path: 'repo',
    component: RepositoryListComponent,
}, {
    path: 'team',
    component: ManageTeamComponent,
}, {
    path: 'settings',
    component: ManageSettingsComponent,
}, {
    path: 'repo/:id',
    component: RepositoryComponent,
}, {
    path: '**',
    component: RepositoryListComponent,
}];

@NgModule({
    imports: [
        BrowserModule,
        MaterialModule,
        RouterModule.forRoot(appRoutes),
        HttpModule,
    ],
    declarations: [
        AppComponent,
        ManageAddressComponent,
        ManageSettingsComponent,
        ManageTeamComponent,
        RepositoryComponent,
        RepositoryListComponent,
    ],
    providers: [
        UserService,
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

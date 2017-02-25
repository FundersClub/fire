import { ApplicationRef, NgModule } from '@angular/core';
import { BrowserModule }  from '@angular/platform-browser';
import { HttpModule } from '@angular/http';
import { MaterialModule } from '@angular/material';

import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';
import { PageNotFoundComponent } from './not-found.component';
import { RepositoryModule } from './repository/repository.module';
import { UserIsAuthedGuard } from './user-auth.service';
import { UserService } from './user.service';

@NgModule({
    imports: [
        BrowserModule,
        HttpModule,
        MaterialModule,
        // Order of the following modules is important.
        RepositoryModule,
        AppRoutingModule,
    ],
    declarations: [
        AppComponent,
        PageNotFoundComponent,
    ],
    providers: [
        UserIsAuthedGuard,
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

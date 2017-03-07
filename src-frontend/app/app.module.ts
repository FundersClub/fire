import { ApplicationRef, NgModule } from '@angular/core';
import { BrowserModule }  from '@angular/platform-browser';
import { HttpModule, XSRFStrategy, CookieXSRFStrategy } from '@angular/http';
import { MaterialModule } from '@angular/material';

import { AppComponent } from './app.component';
import { AppRoutingModule } from './app-routing.module';
import { AssociateEmailModule } from './associate-email/associate-email.module'
import { AuthModule } from './auth-github/auth.module';
import { INITIAL_DATA_CACHE } from './initial-data-cache';
import { PageNotFoundComponent } from './not-found.component';
import { RepositoryModule } from './repository/repository.module';

@NgModule({
    imports: [
        BrowserModule,
        HttpModule,
        MaterialModule,
        // Order of the following modules is important because
        // they have Routers within them.
        AssociateEmailModule,
        AuthModule,
        RepositoryModule,
        AppRoutingModule,
    ],
    declarations: [
        AppComponent,
        PageNotFoundComponent,
    ],
    providers: [
        {
            provide: XSRFStrategy,
            useValue: new CookieXSRFStrategy('csrftoken', 'X-CSRFToken'),
        },
        {
            provide: INITIAL_DATA_CACHE,
            // Inject serverside data if we got it.
            useFactory: () => window['ME_DATA']
        },
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

import { ApplicationRef, NgModule } from '@angular/core';
import { BrowserModule }  from '@angular/platform-browser';
import { AppComponent } from './app.component';

@NgModule({
    imports: [
        BrowserModule
    ],
    declarations: [
        AppComponent
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

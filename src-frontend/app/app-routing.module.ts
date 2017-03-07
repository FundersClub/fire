import { NgModule }              from '@angular/core';
import { RouterModule, Routes }  from '@angular/router';

import { PageNotFoundComponent } from './not-found.component';

const appRoutes: Routes = [{
    path: '**',
    component: PageNotFoundComponent,
    data: {
        title: 'Page not found'
    }
}];

@NgModule({
    imports: [
        RouterModule.forRoot(appRoutes),
    ],
    exports: [
        RouterModule,
    ],
})
export class AppRoutingModule {}

import { NgModule }              from '@angular/core';
import { RouterModule, Routes }  from '@angular/router';

import { AssociateEmailComponent } from './associate-email.component';
import { AssociateEmailResolver } from './associate-email-resolver.service';
import { CurrentUserResolver } from './current-user-resolver.service';

const associateEmailRoutes: Routes = [{
    path: 'associate-email/:uuid',
    component: AssociateEmailComponent,
    resolve: {
        associateEmail: AssociateEmailResolver,
        user: CurrentUserResolver,
    },
    data: {
        title: 'Associate email'
    }
}];

@NgModule({
    imports: [
        RouterModule.forChild(associateEmailRoutes)
    ],
    exports: [
        RouterModule
    ]
})
export class AssociateEmailRoutingModule {}

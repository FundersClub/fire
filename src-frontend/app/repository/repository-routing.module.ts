import { NgModule }              from '@angular/core';
import { RouterModule, Routes }  from '@angular/router';

import { ManageAddressComponent } from './management/manage-address.component';
import { ManageSettingsComponent } from './management/manage-settings.component';
import { ManageTeamComponent } from './management/manage-team.component';
import { OnboardingComponent } from './onboarding/onboarding.component';
import { RepositoryComponent } from './repository.component';
import { RepositoryListComponent } from './repository-list.component';
import { RepositoryResolver } from './repository-resolver.service';
import { SetEmailComponent } from './onboarding/set-email.component';
import { SetTeamComponent } from './onboarding/set-team.component';
import { UserIsAuthedGuard } from '../user-auth.service';

const repositoryRoutes: Routes = [{
    path: 'repos',
    canActivate: [UserIsAuthedGuard],
    children: [{
        path: '',
        component: RepositoryListComponent,
    }, {
        path: ':login/:name',
        resolve: {
            repository: RepositoryResolver,
        },
        children: [{
            path: 'set-up',
            component: OnboardingComponent,
            children: [{
                path: 'email',
                component: SetEmailComponent,
            }, {
                path: 'team',
                component: SetTeamComponent,
            }]
        }, {
            path: '',
            component: RepositoryComponent,
            children: [{
                path: 'team',
                component: ManageTeamComponent,
            }, {
                path: 'settings',
                component: ManageSettingsComponent,
            }, {
                path: '',
                component: ManageAddressComponent,
            }]
        }],
    }],
}];

@NgModule({
    imports: [
        RouterModule.forChild(repositoryRoutes)
    ],
    exports: [
        RouterModule
    ]
})
export class RepositoryRoutingModule {}

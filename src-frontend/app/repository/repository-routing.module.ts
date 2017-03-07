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
import { UserIsAuthedGuard } from '../auth-github/user-auth.service';

const repositoryRoutes: Routes = [{
    path: 'repos',
    canActivate: [UserIsAuthedGuard],
    children: [{
        path: '',
        component: RepositoryListComponent,
        data: {
            title: 'Repositories'
        }
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
                data: {
                    progressBarValue: 33,
                    title: 'Choose an email'
                }
            }, {
                path: 'team',
                component: SetTeamComponent,
                data: {
                    progressBarValue: 66,
                    title: 'Add your team'
                }
            }]
        }, {
            path: '',
            component: RepositoryComponent,
            children: [{
                path: 'team',
                component: ManageTeamComponent,
                data: {
                    title: 'Team'
                }
            }, {
                path: 'settings',
                component: ManageSettingsComponent,
                data: {
                    title: 'Settings'
                }
            }, {
                path: '',
                component: ManageAddressComponent,
                data: {
                    title: 'Send'
                }
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

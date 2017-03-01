import { NgModule }              from '@angular/core';
import { RouterModule, Routes }  from '@angular/router';

import { ManageAddressComponent } from './manage-address.component';
import { ManageSettingsComponent } from './manage-settings.component';
import { ManageTeamComponent } from './manage-team.component';
import { RepositoryComponent } from './repository.component';
import { RepositoryListComponent } from './repository-list.component';
import { RepositoryResolver } from './repository-resolver.service';
import { UserIsAuthedGuard } from '../user-auth.service';

const repositoryRoutes: Routes = [{
    path: 'repos',
    canActivate: [UserIsAuthedGuard],
    children: [{
        path: '',
        component: RepositoryListComponent,
    }, {
        path: ':login/:name',
        component: RepositoryComponent,
        resolve: {
            repository: RepositoryResolver,
        },
        children: [{
            path: '',
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

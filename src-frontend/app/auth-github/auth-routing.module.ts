import { NgModule }              from '@angular/core';
import { RouterModule, Routes }  from '@angular/router';

import { AuthenticateGitHubComponent } from './authenticate-github.component';
import { UserCantApproveRepoGuard } from './wrong-user.service';
import { UserHasAddedGitHubGuard } from './user-has-github.service';
import { WrongUserComponent } from './wrong-user.component';

const authRoutes: Routes = [{
    path: 'authenticate',
    component: AuthenticateGitHubComponent,
}, {
    path: 'approve',
    canActivate: [UserHasAddedGitHubGuard],
    children: [{
        path: ':uuid',
        canActivate: [UserCantApproveRepoGuard],
        component: WrongUserComponent,
    }],
}];

@NgModule({
    imports: [
        RouterModule.forChild(authRoutes)
    ],
    exports: [
        RouterModule
    ]
})
export class AuthRoutingModule {}

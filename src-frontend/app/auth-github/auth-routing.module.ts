import { NgModule }              from '@angular/core';
import { RouterModule, Routes }  from '@angular/router';

import { AuthenticateGitHubComponent } from './authenticate-github.component';
import { BasicRepositoryInfoResolver } from './basic-repo-info.service';
import { LoginComponent } from './login.component';
import { UserCantApproveRepoGuard } from './wrong-user.service';
import { WrongUserComponent } from './wrong-user.component';

const authRoutes: Routes = [{
    path: 'login',
    component: LoginComponent,
}, {
    path: 'authenticate/:uuid',
    component: AuthenticateGitHubComponent,
    resolve: {
        repository: BasicRepositoryInfoResolver,
    }
}, {
    path: 'approve/:uuid',
    canActivate: [UserCantApproveRepoGuard],
    component: WrongUserComponent,
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

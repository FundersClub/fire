import { NgModule }              from '@angular/core';
import { RouterModule, Routes }  from '@angular/router';

import { AuthenticateGitHubComponent } from './authenticate-github.component';
import { BasicRepositoryInfoResolver } from './basic-repo-info.service';
import { CurrentUserResolver } from '../associate-email/current-user-resolver.service';
import { LoginComponent } from './login.component';
import { UserCantApproveRepoGuard } from './wrong-user.service';
import { WrongUserComponent } from './wrong-user.component';

const authRoutes: Routes = [{
    path: 'login',
    component: LoginComponent,
    data: {
        title: 'Login'
    }
}, {
    // Shown to logged-out users, so it can't fetch repo info (the approve
    // endpoint requires authentication).
    path: 'authenticate/:uuid',
    component: AuthenticateGitHubComponent,
    data: {
        title: 'Verify your GitHub'
    }
}, {
    path: 'approve/:uuid',
    canActivate: [UserCantApproveRepoGuard],
    component: WrongUserComponent,
    resolve: {
        repository: BasicRepositoryInfoResolver,
        user: CurrentUserResolver,
    },
    data: {
        title: 'Incorrect user'
    },
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

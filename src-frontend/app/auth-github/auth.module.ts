import { NgModule }       from '@angular/core';
import { CommonModule }   from '@angular/common';
import { MaterialModule } from '@angular/material';

import { AuthenticateGitHubComponent } from './authenticate-github.component';
import { AuthRoutingModule } from './auth-routing.module';
import { BasicRepositoryInfoResolver } from './basic-repo-info.service';
import { LoginComponent } from './login.component';
import { OauthUrlService } from './oauth-url.service'
import { RepositoryService } from '../repository/repository.service';
import { UserCantApproveRepoGuard } from './wrong-user.service';
import { WrongUserComponent } from './wrong-user.component';

@NgModule({
    imports: [
        CommonModule,
        MaterialModule,
        AuthRoutingModule,
    ],
    declarations: [
        AuthenticateGitHubComponent,
        WrongUserComponent,
        LoginComponent,
    ],
    providers: [
        BasicRepositoryInfoResolver,
        OauthUrlService,
        UserCantApproveRepoGuard,
    ],
})
export class AuthModule {}

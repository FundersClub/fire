import { NgModule }       from '@angular/core';
import { CommonModule }   from '@angular/common';
import { MaterialModule } from '@angular/material';

import { AuthenticateGitHubComponent } from './authenticate-github.component';
import { AuthRoutingModule } from './auth-routing.module';
import { RepositoryService } from '../repository/repository.service';
import { UserCantApproveRepoGuard } from './wrong-user.service';
import { UserHasAddedGitHubGuard } from './user-has-github.service';
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
    ],
    providers: [
        UserCantApproveRepoGuard,
        UserHasAddedGitHubGuard,
    ],
})
export class AuthModule {}

import { NgModule }       from '@angular/core';
import { CommonModule }   from '@angular/common';
import { FormsModule }   from '@angular/forms';
import { MaterialModule } from '@angular/material';

import { EditAddressComponent } from './management/edit-address.component';
import { EditTeamComponent } from './management/edit-team.component';
import { EmailMapAddComponent } from './email-map/email-map-add.component';
import { EmailMapEditComponent } from './email-map/email-map-edit.component';
import { ManageAddressComponent } from './management/manage-address.component';
import { ManageSettingsComponent } from './management/manage-settings.component';
import { ManageTeamComponent } from './management/manage-team.component';
import { OnboardingComponent } from './onboarding/onboarding.component';
import { RepositoryComponent } from './repository.component';
import { RepositoryListComponent } from './repository-list.component';
import { RepositoryResolver } from './repository-resolver.service';
import { RepositoryRoutingModule } from './repository-routing.module';
import { RepositoryService } from './repository.service';
import { SetEmailComponent } from './onboarding/set-email.component';
import { SetTeamComponent } from './onboarding/set-team.component';

@NgModule({
    imports: [
        CommonModule,
        FormsModule,
        MaterialModule,
        RepositoryRoutingModule,
    ],
    declarations: [
        EditAddressComponent,
        EditTeamComponent,
        EmailMapAddComponent,
        EmailMapEditComponent,
        ManageAddressComponent,
        ManageSettingsComponent,
        ManageTeamComponent,
        OnboardingComponent,
        RepositoryComponent,
        RepositoryListComponent,
        SetEmailComponent,
        SetTeamComponent,
    ],
    providers: [
        RepositoryResolver,
        RepositoryService,
    ],
})
export class RepositoryModule {}

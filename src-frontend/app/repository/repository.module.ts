import { NgModule }       from '@angular/core';
import { CommonModule }   from '@angular/common';
import { FormsModule }   from '@angular/forms';
import { MaterialModule } from '@angular/material';

import { EditAddressComponent } from './edit-address.component';
import { EmailMapComponent } from './email-map/email-map.component';
import { ManageAddressComponent } from './manage-address.component';
import { ManageSettingsComponent } from './manage-settings.component';
import { ManageTeamComponent } from './manage-team.component';
import { RepositoryComponent } from './repository.component';
import { RepositoryListComponent } from './repository-list.component';
import { RepositoryResolver } from './repository-resolver.service';
import { RepositoryRoutingModule } from './repository-routing.module';
import { RepositoryService } from './repository.service';

@NgModule({
    imports: [
        CommonModule,
        FormsModule,
        MaterialModule,
        RepositoryRoutingModule,
    ],
    declarations: [
        EditAddressComponent,
        EmailMapComponent,
        ManageAddressComponent,
        ManageSettingsComponent,
        ManageTeamComponent,
        RepositoryComponent,
        RepositoryListComponent,
    ],
    providers: [
        RepositoryResolver,
        RepositoryService,
    ],
})
export class RepositoryModule {}

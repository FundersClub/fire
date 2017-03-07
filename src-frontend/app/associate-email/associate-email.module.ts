import { NgModule }       from '@angular/core';
import { CommonModule }   from '@angular/common';
import { MaterialModule } from '@angular/material';

import { AssociateEmailComponent } from './associate-email.component';
import { AssociateEmailResolver } from './associate-email-resolver.service';
import { AssociateEmailRoutingModule } from './associate-email-routing.module';
import { AssociateEmailService } from './associate-email.service';
import { CurrentUserResolver } from './current-user-resolver.service';

@NgModule({
    imports: [
        CommonModule,
        MaterialModule,
        AssociateEmailRoutingModule,
    ],
    declarations: [
        AssociateEmailComponent,
    ],
    providers: [
        AssociateEmailResolver,
        AssociateEmailService,
        CurrentUserResolver,
    ],
})
export class AssociateEmailModule {}

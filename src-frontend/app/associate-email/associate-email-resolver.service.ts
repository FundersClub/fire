import { Injectable } from '@angular/core';
import { Router, Resolve, ActivatedRouteSnapshot } from '@angular/router';

import { AssociateEmail } from './associate-email.model';
import { AssociateEmailService } from './associate-email.service';

@Injectable()
export class AssociateEmailResolver implements Resolve<AssociateEmail> {
    constructor(
        private associateEmailService: AssociateEmailService,
        private router: Router
    ) {}

    resolve(route: ActivatedRouteSnapshot): Promise<AssociateEmail> {
        const uuid = route.params['uuid'];
        return this.associateEmailService.getByUuid(uuid)
            .then((associateEmail) => associateEmail)
            .catch((error) => {
                // No email found... 404.
                this.router.navigate(['/404']);
                return null;
            });
    }
}

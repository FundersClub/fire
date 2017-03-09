import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { AssociateEmail } from './associate-email.model';
import { AssociateEmailService } from './associate-email.service';
import { OauthUrlService } from '../auth-github/oauth-url.service'
import { User } from '../auth-github/user.model';

@Component({
    templateUrl: './associate-email.component.html'
})
export class AssociateEmailComponent implements OnInit {
    associateEmail: AssociateEmail;
    confirming = false;
    error: Object;
    loginUrl = '';
    showConfirmationMessage = false;
    user: User;
    usernameAlreadySet = false;

    constructor(
        private associateEmailService: AssociateEmailService,
        private oAuthUrlService: OauthUrlService,
        private route: ActivatedRoute,
    ) {}

    ngOnInit() {
        let data = this.route.snapshot.data as {
            associateEmail: AssociateEmail,
            user: User,
        };
        this.associateEmail = data.associateEmail;
        this.usernameAlreadySet = !!this.associateEmail.login;
        this.user = data.user;
        this.loginUrl = this.oAuthUrlService.get('/' + this.route.snapshot.url.join('/'))
    }

    confirm() {
        this.confirming = true;
        this.error = null;
        this.associateEmailService.confirmCurrentUserAssociation(this.associateEmail)
            .then(() => this.showConfirmationMessage = true)
            .catch((error) => this.error = error)
            .finally(() => this.confirming = false);
    }
}

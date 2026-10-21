import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { OauthUrlService } from './oauth-url.service'

@Component({
    templateUrl: './authenticate-github.component.html'
})
export class AuthenticateGitHubComponent implements OnInit {
    oAuthUrl: string;

    constructor(
        private oAuthUrlService: OauthUrlService,
        private route: ActivatedRoute
    ) {}

    ngOnInit() {
        let returnTo = this.route.snapshot.queryParams['returnTo'] || '/repos';
        this.oAuthUrl = this.oAuthUrlService.get(returnTo);
    }
}

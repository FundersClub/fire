import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { OauthUrlService } from './oauth-url.service'

@Component({
    templateUrl: './login.component.html',
    styles: [`
        .GitHubLogo {
            left: -2px;
            position: relative;
            top: -2px;
        }
    `],
})
export class LoginComponent implements OnInit {
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

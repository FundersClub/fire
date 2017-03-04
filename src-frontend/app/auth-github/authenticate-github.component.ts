import { Component, OnInit, Inject } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { DOCUMENT } from '@angular/platform-browser'

@Component({
    templateUrl: './authenticate-github.component.html',
    styles: [`
        .GitHubLogo {
            left: -2px;
            position: relative;
            top: -2px;
        }
    `],
})
export class AuthenticateGitHubComponent implements OnInit {
    readonly oAuthUrlBase = '/accounts/github/login/?process=login&next=';
    oAuthUrl: string;
    // This page can display as either a vanilla "login now" page, or the more
    // nuanced "verify now" page (during firebot approval). This will probably
    // change someday when the "verify" flow gets fancier.
    displayAsVerify = false;;

    constructor(
        @Inject(DOCUMENT) private document: any,
        private route: ActivatedRoute
    ) {}

    ngOnInit() {
        let returnTo = this.route.snapshot.queryParams['returnTo'];
        this.displayAsVerify = returnTo.startsWith('/approve');
        this.oAuthUrl = this.document.location.origin + this.oAuthUrlBase + returnTo;
    }
}

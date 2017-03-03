import { Component, OnInit, Inject } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { DOCUMENT } from '@angular/platform-browser'

@Component({
    templateUrl: './authenticate-github.component.html',
})
export class AuthenticateGitHubComponent implements OnInit {
    readonly oAuthUrlBase = '/accounts/github/login/?process=login&next=';
    oAuthUrl: string;

    constructor(
        @Inject(DOCUMENT) private document: any,
        private route: ActivatedRoute
    ) {}

    ngOnInit() {
        this.oAuthUrl = (
            this.document.location.origin +
            this.oAuthUrlBase +
            this.route.snapshot.queryParams['repo']
        );
    }
}

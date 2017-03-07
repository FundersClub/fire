import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { OauthUrlService } from './oauth-url.service'
import { Repository } from '../repository/repository.model';

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
    oAuthUrl: string;
    repository: Repository;

    constructor(
        private oAuthUrlService: OauthUrlService,
        private route: ActivatedRoute
    ) {}

    ngOnInit() {
        let data = this.route.snapshot.data as { repository: Repository };
        this.repository = data.repository;
        let returnTo = this.route.snapshot.queryParams['returnTo'] || '/repos';
        this.oAuthUrl = this.oAuthUrlService.get(returnTo);
    }
}

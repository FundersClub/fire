import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { EmailMap } from './email-map/email-map.model';
import { Repository } from './repository.model';

@Component({
    selector: 'manage-team',
    templateUrl: './manage-team.component.html',
})
export class ManageTeamComponent implements OnInit {
    emailMaps: EmailMap[];
    repositoryUrl: string;

    constructor(
        private route: ActivatedRoute,
    ) {}

    ngOnInit() {
        this.route.data.subscribe((data: { repository: Repository }) => {
            this.emailMaps = data.repository.emailmap_set;
            this.repositoryUrl = data.repository.url;
        });
    }
}

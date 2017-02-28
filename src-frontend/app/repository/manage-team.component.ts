import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { EmailMap } from './email-map/email-map.model';
import { Repository } from './repository.model';
import { RepositoryService } from './repository.service';

@Component({
    selector: 'manage-team',
    styleUrls: ['./manage-team.component.css'],
    templateUrl: './manage-team.component.html',
})
export class ManageTeamComponent implements OnInit {
    emailMaps: EmailMap[];
    repository: Repository;

    constructor(
        private route: ActivatedRoute,
        private respositoryService: RepositoryService,
    ) {}

    ngOnInit() {
        // Always pull a fresh copy of the repo when creating the view. The
        // cached copy in the route's data may be outdatted.
        let data = this.route.snapshot.data as { repository: Repository };
        this.repository = this.respositoryService.getByUrl(data.repository.url);
    }

    trackByFn(index: number, emailMap: EmailMap) {
        return emailMap.url;
    }
}

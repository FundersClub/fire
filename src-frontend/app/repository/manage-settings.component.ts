import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { Repository } from './repository.model';
import { RepositoryService } from './repository.service';

@Component({
    selector: 'manage-settings',
    templateUrl: './manage-settings.component.html',
})
export class ManageSettingsComponent {
    repository: Repository;
    dataDeleted = false;

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

    purge() {
        this.respositoryService.purgeAttachmentData(this.repository)
            .then(() => this.dataDeleted = true);
    }
}

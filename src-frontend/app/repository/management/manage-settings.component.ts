import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { Repository } from '../repository.model';
import { RepositoryService } from '../repository.service';

@Component({
    templateUrl: './manage-settings.component.html',
})
export class ManageSettingsComponent {
    repository: Repository;
    dataDeleted = false;
    saving = false;
    purging = false;
    purgeFailed = false;
    options: any;

    constructor(
        private route: ActivatedRoute,
        private repositoryService: RepositoryService,
    ) {}

    ngOnInit() {
        // Always pull a fresh copy of the repo when creating the view. The
        // cached copy in the route's data may be outdatted.
        let data = this.route.parent.snapshot.data as { repository: Repository };
        this.repository = this.repositoryService.getByUrl(data.repository.url);
        this.options = {
            include_sender_email_in_issue: this.repository.include_sender_email_in_issue,
        };
    }

    purge() {
        if (this.purging) {
            return;
        }
        this.purging = true;
        this.purgeFailed = false;
        this.repositoryService.purgeAttachmentData(this.repository)
            .then(() => {
                this.purging = false;
                this.dataDeleted = true;
            })
            .catch(() => {
                this.purging = false;
                this.purgeFailed = true;
            });
    }

    save() {
        this.saving = true;
        this.repositoryService.updateOptions(this.repository, this.options)
            .then((updatedRepository) => { this.saving = false; })
            .catch((errorMessage: string) => {
                this.saving = false;
            });
    }

}

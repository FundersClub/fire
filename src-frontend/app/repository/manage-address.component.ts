import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { Repository } from './repository.model';
import { RepositoryService } from './repository.service';

@Component({
    templateUrl: './manage-address.component.html',
    styleUrls: ['./manage-address.component.scss']
})
export class ManageAddressComponent implements OnInit {
    repository: Repository;
    inEditMode: boolean = false;

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

    startEditing() {
        this.inEditMode = true;
    }

    editCanceled() {
        this.inEditMode = false;
    }

    editSaved(updatedRepository: Repository) {
        this.repository = updatedRepository;
        this.inEditMode = false;
    }
}

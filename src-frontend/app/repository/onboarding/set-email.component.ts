import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';

import { Repository } from '../repository.model';
import { RepositoryService } from '../repository.service';

@Component({
    templateUrl: './set-email.component.html'
})
export class SetEmailComponent implements OnInit {
    errorMessage = '';
    newAddress: string;
    repository: Repository;
    saving = false;

    constructor(
        private repositoryService: RepositoryService,
        private route: ActivatedRoute,
        private router: Router
    ) {}

    ngOnInit() {
        let data = this.route.parent.snapshot.data as { repository: Repository };
        this.repository = this.repositoryService.getByUrl(data.repository.url);
        this.newAddress = this.repository.email_slug;
    }

    save() {
        this.saving = true;
        this.errorMessage = '';
        this.repositoryService.updateAddress(this.repository, this.newAddress)
            .then(() => {
                this.router.navigate(
                    ['../team'],
                    { relativeTo: this.route }
                );
            })
            .catch((errorMessage: string) => {
                this.saving = false;
                this.errorMessage = errorMessage
            });
    }
}

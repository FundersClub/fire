import { Component, OnInit, EventEmitter, Input, Output } from '@angular/core';

import { Repository } from './repository.model';
import { RepositoryService } from './repository.service';

@Component({
    selector: 'edit-address',
    templateUrl: './edit-address.component.html',
})
export class EditAddressComponent implements OnInit {
    @Input() repository: Repository;
    @Output() editCanceled = new EventEmitter();
    @Output() editSaved = new EventEmitter();
    newAddress: string;
    errorMessage: string;

    constructor(
        private repositoryService: RepositoryService,
    ) {}

    ngOnInit() {
        this.newAddress = this.repository.email_slug;
        this.errorMessage = '';
    }

    cancel() {
        this.editCanceled.emit();
    }

    save() {
        this.errorMessage = '';
        this.repositoryService.updateAddress(this.repository, this.newAddress)
            .then(() => this.editSaved.emit())
            .catch((errorMessage: string) => this.errorMessage = errorMessage);
    }
}

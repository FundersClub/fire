import { Component } from '@angular/core';

import { RepositoryService } from './repository.service';

@Component({
    selector: 'repository-list',
    styleUrls: ['./repository-list.component.scss'],
    templateUrl: './repository-list.component.html',
})
export class RepositoryListComponent {
    constructor(private repositoryService: RepositoryService) {}
}

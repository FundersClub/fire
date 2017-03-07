import { Component, Input } from '@angular/core';

import { EmailMap } from '../email-map/email-map.model';
import { Repository } from '../repository.model';

@Component({
    selector: 'edit-team',
    styleUrls: ['./edit-team.component.scss'],
    templateUrl: './edit-team.component.html',
})
export class EditTeamComponent {
    @Input() repository: Repository;

    constructor() {}

    trackByFn(index: number, emailMap: EmailMap) {
        return emailMap.url;
    }
}

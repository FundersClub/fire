import { Injectable } from '@angular/core';
import { Router, Resolve, ActivatedRouteSnapshot } from '@angular/router';

import { Repository } from './repository.model';
import { RepositoryService } from './repository.service';

@Injectable()
export class RepositoryResolver implements Resolve<Repository> {
    constructor(
        private respositoryService: RepositoryService,
        private router: Router
    ) {}

    resolve(route: ActivatedRouteSnapshot): Repository {
        // Ensure a repo with the specified info actually exists.
        const repository = this.respositoryService.get(
            route.params['login'],
            route.params['name']
        )
        if (repository) {
            return repository;
        } else {
            this.router.navigate(['/repos']);
            return null;
        }
    }
}

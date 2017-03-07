import { Injectable } from '@angular/core';
import { Http } from '@angular/http';

import 'rxjs/add/operator/toPromise';

import { User } from './user.model';
import { RepositoryService } from '../repository/repository.service';

@Injectable()
export class UserService {
    private getUserDataUrl = '/api/github/me/';
    userData: Promise<User>;

    constructor(
        private http: Http,
        private repositoryService: RepositoryService
    ) {
        this.userData = new Promise((resolve, reject) => {
            this.http.get(this.getUserDataUrl).toPromise()
                .then((response) => {
                    let user = response.json() as User;
                    resolve(user);
                    // Cache data.
                    if (user && user.repositories) {
                        for (let repo of user.repositories) {
                            this.repositoryService.add(repo);
                        }
                    }
                })
                .catch((error: any) => {
                    console.error('Error:', error);
                    reject(error);
                });
            }
        );
    }

    isAuthenticated(): Promise<boolean> {
        return this.userData.then((user: User) => user.is_authenticated);
    }
}

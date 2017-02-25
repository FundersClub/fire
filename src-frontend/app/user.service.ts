import { Injectable } from '@angular/core';
import { Http } from '@angular/http';

import 'rxjs/add/operator/toPromise';

import { User } from './user.model';
import { RepositoryService } from './repository/repository.service';

const USER_DATA = {
    "username": "youpdidou",
    "is_authenticated": true,
    "repositories": [
        {
            "emailmap_set": [
                {
                    "email": "alexandre.scialom@gmail.com",
                    "login": "youpdidou",
                    "repo": "http://localhost:12000/api/github/repository/4/",
                    "url": "http://localhost:12000/api/github/email-map/3/"
                },
                {
                    "email": "alexandre@fundersclub.com",
                    "login": "youpdidou",
                    "repo": "http://localhost:12000/api/github/repository/4/",
                    "url": "http://localhost:12000/api/github/email-map/4/"
                }
            ],
            "email": "46f48eac@firebot.fundersclub.com",
            "email_slug": "46f48eac",
            "full_name": "youpdidou/buzz",
            "gh_url": "https://github.com/youpdidou/buzz",
            "login": "youpdidou",
            "name": "buzz",
            "status": "active",
            "url": "http://localhost:12000/api/github/repository/4/"
        }
    ],
    "urls": {
        "logout": "http://localhost:12000/accounts/logout/"
    }
};


@Injectable()
export class UserService {
    private getUserDataUrl = 'api/github/me/';
    private userData: Promise<User>;

    constructor(
        private http: Http,
        private repositoryService: RepositoryService
    ) {
        // Get our data in place!
        // let p = this.http.get(this.getUserDataUrl)
        //     .toPromise()
        //     .then(response => response.json() as User)
        //     .catch(this.handleError);
        this.userData = Promise.resolve(USER_DATA);

        // Update other services.
        this.userData.then((user: User) => {
            // Cache data.
            if (user && user.repositories) {
                for (let repo of user.repositories) {
                    this.repositoryService.add(repo);
                }
            }
        });
    }

    isAuthenticated(): Promise<boolean> {
        return this.userData.then((user: User) => user.is_authenticated);
    }

    // private handleError(error: any): Promise<any> {
    //     console.error('Error', error);
    //     return Promise.reject(error && (error.message || error) || {});
    // }
}

export class EmailMap {
    constructor(
        public email: string,
        public login: string,  // Github handle
        public repo: string,  // API URL to repo: http://localhost:12000/api/github/repository/4/
        public url?: string
    ) {}
}

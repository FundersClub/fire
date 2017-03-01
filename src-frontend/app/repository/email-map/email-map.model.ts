export class EmailMap {
    constructor(
        public email: string,
        public login: string,  // Github handle
        public repo: string,  // API URL to repo
        public url?: string
    ) {}
}

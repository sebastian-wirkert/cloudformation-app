
// HOW TO INCLUDE APOLLO:
// HTTPS://MEDIUM.COM/@GUILLAC124/CREATE-YOUR-CUSTOM-APOLLO-CLIENT-FOR-AWS-APPSYNC-TO-USE-HOOKS-2D5CBCE29DB5
import { createAuthLink } from 'aws-appsync-auth-link';
import Auth from '@aws-amplify/auth'
import { ApolloClient, InMemoryCache, createHttpLink, ApolloLink} from '@apollo/client' 
import config from '../../aws-exports'

const url = config.graphQlEndpoint;
const region = config.region;
const auth = {
  type: config.mainGraphQLAuthenticationMethod,
  credentials: () => Auth.currentCredentials(),
  jwtToken: async () =>
    (await Auth.currentSession()).getAccessToken().getJwtToken()
}
const link = ApolloLink.from([
   createAuthLink({ url, region, auth }), 
   createHttpLink({ uri: url })
]);

export function getApolloClient() {
    return new ApolloClient({
        link,
        cache: new InMemoryCache()
    });      
}
import { StatusBar } from 'expo-status-bar';
import React from 'react';
import { StyleSheet, Text, View, Button } from 'react-native';
import Auth from '@aws-amplify/auth'
import config from './aws_config'
import {getApolloClient} from './src/api/apolloClient'
import { ApolloProvider, gql } from '@apollo/client'


client = getApolloClient()

export default class App extends React.PureComponent{

  constructor(props){
    super(props)
    this.state = {
      text: ""
    }
  }

  signIn() {
    Auth.signIn("test@test.de", "testpw").
      then(mes => 
        {
          this.setState({text: "logged in Testuser"})
        }).
      catch(err => {this.setState({text: "login failed"})})
  }

  signOut() {
    Auth.signOut().
      then(mes => 
        {
          this.setState({text: "logged out Testuser"})
          
        }).
      catch(err => {this.setState({text: "login failed"})})
  }

  fakeDelete() {
    const DELETE_SHOW = gql`
      mutation fakeDelete {
        deleteShow(sID: 3) {
          description
          sName
        }
      }
    `;
    client.mutate({mutation: DELETE_SHOW})
    .then(resp => this.setState({text: resp.data.deleteShow.sName})).catch(e => this.setState({text: e.message}))
  }

  loadShows() {
    const LOAD_SHOWS = gql`
      query queryShows {
        getShow(sID: "3") {
          description
          sName
        }
      }
    `;
    client.query({query: LOAD_SHOWS})
    .then(resp => this.setState({text: resp.data.getShow.sName})).catch(e => this.setState({text: e.message}))
  }

  async componentDidMount(){    
    Auth.configure({
      ...config,
    })
  }

  async getUserID() {
    try {
        let user = await Auth.currentAuthenticatedUser()
        return {payload: {uID: user.attributes.sub}}
    }
    catch (err) {
        return {payload: "error"}
    }
}

  render(){     
    return (      
      <ApolloProvider client={client}>
        <View style={styles.container}>
          <Text>{this.state.text}</Text>
          <Button onPress={() => this.signIn()} title="Sign in" />
          <Button onPress={() => this.signOut()} title="Sign out" />
          <Button onPress={() => this.loadShows()} title="Load Shows" />
          <Button onPress={() => this.fakeDelete()} title="Fake delete" />
          <StatusBar style="auto" />
        </View>
      </ApolloProvider>
    )
  }
}


const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
  },
});

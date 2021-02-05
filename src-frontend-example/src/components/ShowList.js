// Import library to create a component
import React from 'react';
import { Text } from 'react-native';
import { gql, useQuery } from '@apollo/client'

// Create a component
const ShowList = (props) => {
    const GET_FLAVORS = gql`
      query queryShows {
        getShow(sID: "3") {
          description
        }
      }
    `;
    
    try {
      //const {loading, error, data} = useQuery(GET_FLAVORS);
      //console.log({like: "boobss"})
      //console.log({loading, error, data})
    }
    catch (e) {
      console.log({a: "sadfksalfj", e})
    }
     
    //if(loading) return <Text>Loading</Text>   
    //if(error) return <Text>Error</Text>

    return <Text>Loaded</Text>
};


// Make available to other components
export { ShowList };

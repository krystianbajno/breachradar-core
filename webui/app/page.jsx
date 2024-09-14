'use client'
import {
  InstantSearch,
  SearchBox,
  Hits,
  Pagination,
  Stats,
  Configure
} from 'react-instantsearch'
import Client from '@searchkit/instantsearch-client'
import { useState } from "react"

const searchClient = Client({
  url: '/api/search'
})

const HitView = ({ hit, query }) => {
  const results_split = hit.content.split("\r\n")

  const results_filtered = results_split.filter(i => i.includes(query))
  const results = results_filtered.join("\n")
  
  return (
    <div className="hit__details">
      <pre>
        {results}
      </pre>
    </div>
  );
}

export default function Web() {
  const [query, setQuery] = useState('')
  const queryHook = (inputValue, search) => {
    setQuery(inputValue); 
    search(inputValue);   
  };

  return (
    <div className="container">
      <InstantSearch 
        indexName="scrapes_chunks"
        searchClient={searchClient} 
        routing
      >
        <div className="search-panel">
          <div className="search-panel__filters">
            <div className="searchbox">
              <SearchBox 
                placeholder="Search in content"
                searchAsYouType={false}
                queryHook={queryHook}
              />
            </div>
            {query && (
              <div className="pagination">
                <Stats />
              </div>
            )}
          </div>

          <div className="search-panel__results">
            {query ? (
              <div>
                <Configure hitsPerPage={2560} query={query} />
                <Hits hitComponent={(props) => <HitView {...props} query={query}/>} />
              </div> 
            ) : (
              <p>Please enter a search query to see results.</p>
            )}
          </div>
        </div>
      </InstantSearch>
    </div>
  )
}

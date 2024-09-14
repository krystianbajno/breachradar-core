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

const HitView = ({ hit }) => {
  const processContent = (content) => {
    const contentWithoutMark = content.replace(/<\/?mark>/g, '') 
    return contentWithoutMark
  }

  return (
    <div>
      <div className="hit__details">
        <pre style={{ width: 600 }}>
          {processContent(hit._highlightResult.content.value)}
        </pre>
      </div>
    </div>
  );
}

export default function Web() {
  const [query, setQuery] = useState('')

  return (
    <div className="">
      <InstantSearch 
        indexName="scrapes_chunks"
        searchClient={searchClient} 
        routing
        onSearchStateChange={({ query }) => setQuery(query || '')}
      >
        <Configure
          hitsPerPage={16}
          query={query}
        />
        <div className="container">
          <div className="search-panel">
            <div className="search-panel__results">
              <div className="searchbox">
                <SearchBox 
                  placeholder="Search in content"
                  searchAsYouType={false}
                />
              </div>

              <Stats />
              <Hits hitComponent={HitView} /> 
              <Pagination />
            </div>
          </div>
        </div>
      </InstantSearch>
    </div>
  )
}

'use client'
import {
  InstantSearch,
  SearchBox,
  Hits,
  Stats,
  Configure,
  useInstantSearch,
  useSearchBox
} from 'react-instantsearch'
import Client from '@searchkit/instantsearch-client'

const searchClient = Client({
  url: '/api/search'
})

const HitView = ({ hit }) => {
  const downloadHitContent = () => {
    const content = hit.filteredContent;
    
    const blob = new Blob([content], { type: 'text/plain' });
    
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `${hit.title.replace(/\s+/g, '_')}_content.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  return (
    <div className="hit__details">
      <div className={"hit-details-panel"}>
        <h3>{hit.title}</h3>
        <button className={'download-btn'} onClick={downloadHitContent}>Download</button>
      </div>
      <pre>{hit.filteredContent}</pre>
    </div>
  )
}

function SearchStatus() {
  const { status } = useInstantSearch();

  if (status === 'loading') {
    return <p>Loading...</p>; 
  }
  
  return null;
}

function CustomHits() {
  const { query } = useSearchBox();
  const { results } = useInstantSearch(); // Get the search results

  if (results.nbHits === 0) {
    return <p>No results found.</p>; // Display a message when no results are found
  }

  // Process hits: split, filter, and join the content
  const processedHits = results.hits
    .map(hit => {
      const resultsSplit = hit.content.split("\r\n"); // Split the content by lines

      // Filter based on the query
      const filteredResults = resultsSplit.filter(line => line.includes(query));

      // Join the filtered results into a single string
      const filteredContent = filteredResults.join("\n");

      return { ...hit, filteredContent };
    })
    .filter(hit => hit.filteredContent.trim() !== '');

  if (processedHits.length === 0) {
    return <p>No relevant content found.</p>; 
  }

  return (
    <div>
      {processedHits.map(hit => (
        <HitView key={hit.objectID} hit={hit} />
      ))}
    </div>
  );
}

export default function Web() {
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
              <SearchBox placeholder="Search in content" searchAsYouType={false} />
            </div>

            <SearchStatus />

            <div className="pagination">
              <Stats />
            </div>
          </div>

          <div className="search-panel__results">
            <Configure hitsPerPage={9999} />
            <CustomHits /> {/* Use CustomHits component to pass the query */}
          </div>
        </div>
      </InstantSearch>
    </div>
  )
}

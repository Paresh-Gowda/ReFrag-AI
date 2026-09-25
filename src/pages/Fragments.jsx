import { useEffect, useMemo, useState } from "react";
import {
  Database,
  Search,
  FileCode2,
  Activity,
} from "lucide-react";

import { getFragments } from "../services/api";
import "../styles/fragments.css";


function Fragments() {
  const [fragments, setFragments] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);


  useEffect(() => {
    async function loadFragments() {
      try {
        const data = await getFragments();

        setFragments(data.fragments || []);
      } catch (error) {
        console.error(
          "Failed to load fragments:",
          error
        );
      } finally {
        setLoading(false);
      }
    }

    loadFragments();
  }, []);


  const filteredFragments = useMemo(() => {
    const query = search.toLowerCase().trim();

    if (!query) {
      return fragments;
    }

    return fragments.filter((fragment) =>
      Object.values(fragment).some((value) =>
        String(value)
          .toLowerCase()
          .includes(query)
      )
    );
  }, [fragments, search]);


  if (loading) {
    return (
      <div className="fragments-page">
        <div className="fragments-loading">
          Loading fragment intelligence...
        </div>
      </div>
    );
  }


  return (
    <div className="fragments-page">

      {/* HEADER */}

      <div className="fragments-header">

        <div>
          <p className="eyebrow">
            FRAGMENT INTELLIGENCE
          </p>

          <h1>
            Storage Fragments
          </h1>

          <p>
            Inspect extracted fragments and
            machine-learning classifications.
          </p>
        </div>


        <div className="fragment-count">
          <Database size={18} />
          {fragments.length} fragments
        </div>

      </div>


      {/* SEARCH */}

      <div className="fragment-search">

        <Search size={17} />

        <input
          type="text"
          placeholder="Search fragment ID, file type, source..."
          value={search}
          onChange={(event) =>
            setSearch(event.target.value)
          }
        />

      </div>


      {/* TABLE */}

      <div className="fragments-table-wrapper">

        <table className="fragments-table">

          <thead>
            <tr>
              <th>FRAGMENT</th>
              <th>FILE TYPE</th>
              <th>SOURCE</th>
              <th>INDEX</th>
              <th>SIZE</th>
              <th>ENTROPY</th>
            </tr>
          </thead>


          <tbody>

            {filteredFragments.map(
              (fragment, index) => {

                const fragmentId =
                  fragment.fragment_id ||
                  fragment.id ||
                  fragment.fragment ||
                  `FRAG_${String(index + 1).padStart(6, "0")}`;

                const fileType =
                  fragment.file_type ||
                  fragment.type ||
                  "UNKNOWN";

                const source =
                  fragment.source_file ||
                  fragment.source ||
                  fragment.source_id ||
                  "—";

                const fragmentIndex =
                  fragment.fragment_index ??
                  fragment.index ??
                  "—";

                const size =
                  fragment.size ??
                  fragment.fragment_size ??
                  "—";

                const entropy =
                  fragment.entropy;

                return (
                  <tr key={fragmentId}>

                    <td>

                      <div className="fragment-id">

                        <FileCode2 size={16} />

                        <strong>
                          {fragmentId}
                        </strong>

                      </div>

                    </td>


                    <td>

                      <span className="file-type">
                        {String(
                          fileType
                        ).toUpperCase()}
                      </span>

                    </td>


                    <td>
                      <span className="source-name">
                        {source}
                      </span>
                    </td>


                    <td>
                      {fragmentIndex}
                    </td>


                    <td>
                      {typeof size === "number"
                        ? `${size.toLocaleString()} B`
                        : size}
                    </td>


                    <td>

                      <div className="entropy">

                        <Activity size={14} />

                        {typeof entropy === "number"
                          ? entropy.toFixed(3)
                          : "—"}

                      </div>

                    </td>

                  </tr>
                );
              }
            )}

          </tbody>

        </table>


        {filteredFragments.length === 0 && (

          <div className="no-fragments">
            No fragments found.
          </div>

        )}

      </div>

    </div>
  );
}


export default Fragments;
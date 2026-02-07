export interface ParsedDocumentSectionDTO {
  title: string;
  description?: string;
  pullet_points?: string[];
}

export interface ParsedDocumentDTO {
  file: string;
  file_hash: string;
  parent_type: string;
  meta_data: dict[str, str];
  parent_id: string;
  sections: ParsedDocumentSectionDTO[];
}

export interface ParsedDocumentParseRequest {
  path: string;
  parent_type: string;
  parent_id: string;
}

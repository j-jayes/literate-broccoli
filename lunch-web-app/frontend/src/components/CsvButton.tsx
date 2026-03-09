import { Button } from "@fluentui/react-components";
import { ArrowDownload24Regular } from "@fluentui/react-icons";
import { getCsvUrl } from "../api";

interface Props {
  sessionId: string;
}

export default function CsvButton({ sessionId }: Props) {
  return (
    <Button
      appearance="secondary"
      icon={<ArrowDownload24Regular />}
      as="a"
      href={getCsvUrl(sessionId)}
      // @ts-ignore - anchor attributes
      download
    >
      Download CSV
    </Button>
  );
}

#! /usr/bin/env python

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ## LUCENENET PORTING NOTES
# This script was originally written for Python 2, but has been tested against Python 3.
# No changes were necessary to run this script in Python 3.

# LUCENENET specific - we write the usings before the header
HEADER="""//------------------------------------------------------------------------------
// <auto-generated>
//     This code was generated by the gen_Direct.py script.
//
//     Changes to this file may cause incorrect behavior and will be lost if
//     the code is regenerated.
// </auto-generated>
//------------------------------------------------------------------------------

namespace Lucene.Net.Util.Packed
{

    /*
     * Licensed to the Apache Software Foundation (ASF) under one or more
     * contributor license agreements.  See the NOTICE file distributed with
     * this work for additional information regarding copyright ownership.
     * The ASF licenses this file to You under the Apache License, Version 2.0
     * (the "License"); you may not use this file except in compliance with
     * the License.  You may obtain a copy of the License at
     *
     *     http://www.apache.org/licenses/LICENSE-2.0
     *
     * Unless required by applicable law or agreed to in writing, software
     * distributed under the License is distributed on an "AS IS" BASIS,
     * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
     * See the License for the specific language governing permissions and
     * limitations under the License.
     */

    using DataInput = Lucene.Net.Store.DataInput;

"""

TYPES = {8: "byte", 16: "short", 32: "int", 64: "long"}
DOTNET_READ_TYPES = {8: "Byte", 16: "Int16", 32: "Int32", 64: "Int64"} # LUCENENET specific
MASKS = {8: " & 0xFFL", 16: " & 0xFFFFL", 32: " & 0xFFFFFFFFL", 64: ""}
CASTS = {8: "(byte)", 16: "(short)", 32: "(int)", 64: ""} # LUCENENET specific - removed space from casts to match existing C# port style

if __name__ == '__main__':
  for bpv in TYPES.keys():
    type
    f = open("Direct%d.cs" %bpv, 'w')

    # LUCENENET specific - we write the usings before the header
    f.write("using Lucene.Net.Diagnostics;\n")
    f.write("using Lucene.Net.Support;\n")
    f.write("using System;\n")
    f.write("using System.Runtime.CompilerServices;\n")

    f.write(HEADER)
    f.write("""    /// <summary>
    /// Direct wrapping of %d-bits values to a backing array.
    /// <para/>
    /// @lucene.internal
    /// </summary>\n""" %bpv)
    f.write("    internal sealed class Direct%d : PackedInt32s.MutableImpl\n" %bpv)
    f.write("    {\n")
    f.write("        private readonly %s[] values;\n\n" %TYPES[bpv])

    f.write("        internal Direct%d(int valueCount)\n" %bpv)
    f.write("            : base(valueCount, %d)\n" %bpv)
    f.write("        {\n")
    f.write("            values = new %s[valueCount];\n" %TYPES[bpv])
    f.write("        }\n\n")

    # LUCENENET specific - remove unused parameter for Direct64
    if bpv == 64:
      f.write("        internal Direct%d(/*int packedIntsVersion,*/ DataInput @in, int valueCount) // LUCENENET specific - removed unused parameter\n" %bpv)
    else:
      f.write("        internal Direct%d(int packedIntsVersion, DataInput @in, int valueCount)\n" %bpv)
    f.write("            : this(valueCount)\n")
    f.write("        {\n")
    if bpv == 8:
      f.write("            @in.ReadBytes(values, 0, valueCount);\n")
    else:
      f.write("            for (int i = 0; i < valueCount; ++i)\n")
      f.write("            {\n")
      f.write("                values[i] = @in.Read%s();\n" %DOTNET_READ_TYPES[bpv].title()) # LUCENENET specific
      f.write("            }\n")
    if bpv != 64:
      f.write("            // because packed ints have not always been byte-aligned\n")
      f.write("            int remaining = (int)(PackedInt32s.Format.PACKED.ByteCount(packedIntsVersion, valueCount, %d) - %dL * valueCount);\n" %(bpv, bpv / 8))
      f.write("            for (int i = 0; i < remaining; ++i)\n")
      f.write("            {\n")
      f.write("                @in.ReadByte();\n")
      f.write("            }\n")
    f.write("        }\n")

    f.write("""
        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        public override long Get(int index)
        {
            return values[index]%s;
        }

        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        public override void Set(int index, long value)
        {
            values[index] = %s(value);
        }

        public override long RamBytesUsed()
        {
            return RamUsageEstimator.AlignObjectSize(
                RamUsageEstimator.NUM_BYTES_OBJECT_HEADER
                + 2 * RamUsageEstimator.NUM_BYTES_INT32     // valueCount,bitsPerValue
                + RamUsageEstimator.NUM_BYTES_OBJECT_REF) // values ref
                + RamUsageEstimator.SizeOf(values);
        }

        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        public override void Clear()
        {
            Arrays.Fill(values, %s0L);
        }

        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        public override object GetArray()
        {
            return values;
        }

        public override bool HasArray => true;
""" %(MASKS[bpv], CASTS[bpv], CASTS[bpv]))

    if bpv == 64:
      f.write("""
        public override int Get(int index, long[] arr, int off, int len)
        {
            if (Debugging.AssertsEnabled)
            {
                Debugging.Assert(len > 0, "len must be > 0 (got {0})", len);
                Debugging.Assert(index >= 0 && index < m_valueCount);
                Debugging.Assert(off + len <= arr.Length);
            }

            int gets = Math.Min(m_valueCount - index, len);
            Arrays.Copy(values, index, arr, off, gets);
            return gets;
        }

        public override int Set(int index, long[] arr, int off, int len)
        {
            if (Debugging.AssertsEnabled)
            {
                Debugging.Assert(len > 0, "len must be > 0 (got {0})", len);
                Debugging.Assert(index >= 0 && index < m_valueCount);
                Debugging.Assert(off + len <= arr.Length);
            }

            int sets = Math.Min(m_valueCount - index, len);
            Arrays.Copy(arr, off, values, index, sets);
            return sets;
        }

        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        public override void Fill(int fromIndex, int toIndex, long val)
        {
            Arrays.Fill(values, fromIndex, toIndex, val);
        }
""")
    else:
      f.write("""
        public override int Get(int index, long[] arr, int off, int len)
        {
            if (Debugging.AssertsEnabled)
            {
                Debugging.Assert(len > 0, "len must be > 0 (got {0})", len);
                Debugging.Assert(index >= 0 && index < m_valueCount);
                Debugging.Assert(off + len <= arr.Length);
            }

            int gets = Math.Min(m_valueCount - index, len);
            for (int i = index, o = off, end = index + gets; i < end; ++i, ++o)
            {
                arr[o] = values[i]%s;
            }
            return gets;
        }

        public override int Set(int index, long[] arr, int off, int len)
        {
            if (Debugging.AssertsEnabled)
            {
                Debugging.Assert(len > 0, "len must be > 0 (got {0})", len);
                Debugging.Assert(index >= 0 && index < m_valueCount);
                Debugging.Assert(off + len <= arr.Length);
            }

            int sets = Math.Min(m_valueCount - index, len);
            for (int i = index, o = off, end = index + sets; i < end; ++i, ++o)
            {
                values[i] = %sarr[o];
            }
            return sets;
        }

        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        public override void Fill(int fromIndex, int toIndex, long val)
        {
            if (Debugging.AssertsEnabled) Debugging.Assert(val == (val%s));
            Arrays.Fill(values, fromIndex, toIndex, %sval);
        }
""" %(MASKS[bpv], CASTS[bpv], MASKS[bpv], CASTS[bpv]))

    f.write("    }\n")
    f.write("}\n")

    f.close()